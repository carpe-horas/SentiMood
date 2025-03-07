import styled from 'styled-components';

const StyledButton = styled.button`
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  background-color: ${(props) => props.bgColor || '#A3C6ED'};
  color: ${(props) => props.color || 'white'};
  font-size: ${(props) => props.size || '16px'};
  transition: background-color 0.3s;

  &:hover {
    background-color: ${(props) => props.hoverColor || '#57a6fa'};
  }
`;

const Button = ({ children, onClick, bgColor, color, size, hoverColor }) => {
  return (
    <StyledButton
      onClick={onClick}
      bgColor={bgColor}
      color={color}
      size={size}
      hoverColor={hoverColor}
    >
      {children}
    </StyledButton>
  );
};

export default Button;